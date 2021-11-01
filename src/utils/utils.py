from pkg_resources import resource_filename
import os

def get_fn(filename):
    """Get the full path to one of the reference files shipped for utils.
    Parameters
    ----------
    filename : str
        Name of the file to load (with respect to the files/ folder).
    Returns
    -------
    fn : str
        Full path to filename
    """
    try:
        fn = resource_filename('waveform_fun', os.path.join('src', 'tests', 'files', filename))
    except ModuleNotFoundError:
        fn = resource_filename('src', os.path.join('tests', 'files', filename))
    if not os.path.exists(fn):
        raise IOError('Sorry! {} does not exists.'.format(fn))
    return fn
