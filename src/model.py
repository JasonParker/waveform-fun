from sklearn.pipeline import Pipeline

def run_pipeline(model, X_train, y_train, X_test, y_test):
    """Run pipeline in SKlearn to fit and make predictions with a model

    Parameters
    ----------
    model :
        Model to use
    X_train : np.array, shape=(nrows, ncolumns)
        Training features
    y_train : np.array, shape=(nrows,)
        Training label to predict
    X_test : np.array, shape=(nrows, ncolumns)
        Test features
    y_test : np.array, shape=(nrows,)
        Test label to predict

    Returns
    -------
    pipeline : sklearn.Pipeline object
        Pipeline of model
    pipeline_predictions : np.array(nrows)
        Predictions from model
    """
    pipeline = Pipeline(steps=[('m', model)])

    pipeline.fit(X_train, y_train)

    pipeline_predictions = pipeline.predict(X_test)

    print_metrics(pipeline, X_test, y_test, pipeline_predictions)

    return pipeline, pipeline_predictions

def run_stratified_pipeline(model, X, y, n_splits=5):
    """Run pipeline in SKlearn to cross-validate model
    Parameters
    ----------
    model :
        Model to use
    X : np.array, shape=(nrows, ncolumns)
        Unsplit features
    y : np.array, shape=(nrows,)
        Unsplit labels to predict
    n_splits : int, default=5
        # of splits for K-fold

    Returns
    -------
    pipeline : sklearn.Pipeline object
        Pipeline of model
    pipeline_predictions : np.array(nrows)
        Predictions from model
    """
    pipeline = make_pipeline(model)
    # Cross validate model
    cv = StratifiedKFold(n_splits=n_splits)
    n_scores = cross_validate(pipeline, X, y, scoring=("recall", "precision", "roc_auc"), cv=cv, error_score="raise")

    # report performance
    print('Recall: %.3f (%.3f)' % (np.mean(n_scores["test_recall"]), np.std(n_scores["test_recall"])))
    print('Precision: %.3f (%.3f)' % (np.mean(n_scores["test_precision"]), np.std(n_scores["test_precision"])))
    print('ROC_AUC: %.3f (%.3f)' % (np.mean(n_scores["test_roc_auc"]), np.std(n_scores["test_roc_auc"])))

    return pipeline, n_scores
