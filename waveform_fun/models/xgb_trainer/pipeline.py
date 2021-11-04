import os
from datetime import datetime

import kfp
from google.cloud import aiplatform
from google_cloud_pipeline_components import aiplatform as gcc_aip
from kfp.v2 import compiler
from kfp.v2.dsl import component
from kfp.v2.google import experimental
from task import main

TIMESTAMP = datetime.now().strftime("%Y%m%d%H%M%S")
PROJECT = os.environ["PROJECT_ID"]
BUCKET = "physionet_2009"
PIPELINE_ROOT = f"gs://{BUCKET}/pipeline_root"
REGION = "us-central1"

OUTDIR = f"gs://{BUCKET}/models/trained_xgb_model_{TIMESTAMP}"
MODEL_DISPLAY_NAME = f"xgb_model_{TIMESTAMP}"

#PYTHON_PACKAGE_URIS = f"gs://{BUCKET}/model_pkgs/abp_xgboost_trainer-0.1.tar.gz"
PYTHON_PACKAGE_URIS = f"gs://{BUCKET}/model_pkgs/waveform_fun-0.0.tar.gz"
MACHINE_TYPE = "n1-standard-16"
REPLICA_COUNT = 1
PYTHON_PACKAGE_EXECUTOR_IMAGE_URI = (
    "us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-3:latest"
)
SERVING_CONTAINER_IMAGE_URI = (
    "us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-3:latest"
)
PYTHON_MODULE = "waveform_fun.models.xgb_trainer.task"

# Model and training hyperparameters
# TODO: DO later
BATCH_SIZE = 500
NUM_EXAMPLES_TO_TRAIN_ON = 10000
NUM_EVALS = 1000
NBUCKETS = 10
LR = 0.001
NNSIZE = "32 8"

# GCS paths
GCS_PROJECT_PATH = f"gs://{BUCKET}/models"
DATA_PATH = f"{GCS_PROJECT_PATH}/processed"

@component
def training_op(input1: str):
    print("VertexAI pipeline: {}".format(input1))
    main()

@kfp.dsl.pipeline(name="abp-xgb--train-upload-endpoint-deploy")
def pipeline(
    project: str = PROJECT,
    model_display_name: str = MODEL_DISPLAY_NAME,
):
    train_task = training_op("hypotension xgb training pipeline")
    experimental.run_as_aiplatform_custom_job(
        train_task,
        display_name=f"pipelines-train-{TIMESTAMP}",
        worker_pool_specs=[
            {
                "pythonPackageSpec": {
                    "executor_image_uri": PYTHON_PACKAGE_EXECUTOR_IMAGE_URI,
                    "package_uris": [PYTHON_PACKAGE_URIS],
                    "python_module": PYTHON_MODULE,
                },
                "replica_count": f"{REPLICA_COUNT}",
                "machineSpec": {
                    "machineType": f"{MACHINE_TYPE}",
                },
            }
        ],
    )

    model_upload_op = gcc_aip.ModelUploadOp(
        project=f"{PROJECT}",
        display_name=f"pipelines-ModelUpload-{TIMESTAMP}",
        artifact_uri=f"{OUTDIR}/savedmodel",
        serving_container_image_uri=f"{SERVING_CONTAINER_IMAGE_URI}",
        serving_container_environment_variables={"NOT_USED": "NO_VALUE"},
    )
    model_upload_op.after(train_task)

    endpoint_create_op = gcc_aip.EndpointCreateOp(
        project=f"{PROJECT}",
        display_name=f"pipelines-EndpointCreate-{TIMESTAMP}",
    )

    model_deploy_op = gcc_aip.ModelDeployOp(
        project=f"{PROJECT}",
        endpoint=endpoint_create_op.outputs["endpoint"],
        model=model_upload_op.outputs["model"],
        deployed_model_display_name=f"{MODEL_DISPLAY_NAME}",
        machine_type=f"{MACHINE_TYPE}",
    )

def run():
    if not os.path.isdir("vertex_pipelines"):
       os.mkdir("vertex_pipelines")

    compiler.Compiler().compile(
        pipeline_func=pipeline,
        package_path="./vertex_pipelines/train_upload_endpoint_deploy.json",
    )

    pipeline_job = aiplatform.pipeline_jobs.PipelineJob(
    display_name="abp_xgb_pipeline",
    template_path="./vertex_pipelines/train_upload_endpoint_deploy.json",
    pipeline_root=f"{PIPELINE_ROOT}",
    project=PROJECT,
    location=REGION,
    )

    pipeline_job.run()

if __name__ == "__main__":
    run()
