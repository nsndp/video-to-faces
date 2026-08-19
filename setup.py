from setuptools import setup, find_packages

setup(
    name='videotofaces',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    include_package_data=True,

    version='0.0.1',
    license='MIT',
    description='A library for extracting faces from videos and grouping them by character using a variety of face detection/recognition models',
    author='nsndp',
    author_email='zagumennov.da@gmail.com',
    url='https://github.com/nsndp/video-to-faces',
    
    python_requires='>=3.6',
    install_requires=[
        'numpy',
        'opencv-python',
        'requests',
        'scikit-learn',
        'torch',
        'torchvision',
        'tqdm',
    ],
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Multimedia :: Video',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

# on package_dir with src structure to support editable installs: https://stackoverflow.com/a/19917117

# helpful links on project structure practices:
# https://github.com/yngvem/python-project-structure
# https://github.com/pypa/sampleproject
# https://blog.ionelmc.ro/2014/05/25/python-packaging/
# https://github.com/ionelmc/python-nameless