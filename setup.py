import setuptools, os

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name="pandiocli",
    version="1.0.7",
    author="Joshua Odmark",
    author_email="josh@pandio.com",
    description="CLI to control Pandio's machine learning service.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/pandio-com/pandiocli",  # usually to github repository
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Documentation",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
    ],
    entry_points={
        "console_scripts": [
            'pandiocli = src.__main__:main'
        ]
    },
    install_requires=['goodconf==1.0.0', 'requests==2.25.1', 'pandioml==1.0.4', 'pyinstaller==4.3', 'Faker==8.1.1',
                      'appdirs==1.4.4', 'requests-toolbelt==0.9.1'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests'
)