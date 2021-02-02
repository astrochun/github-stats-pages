from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fr:
    requirements = fr.read().splitlines()

setup(
    name='github-stats-pages',
    version='0.1.4',
    packages=['tests', 'github_stats_pages'],
    scripts=['scripts/get_repo_list'],
    url='https://github.com/astrochun/github-stats-pages',
    license='MIT',
    author='Chun Ly',
    author_email='astro.chun@gmail.com',
    description='Retrieve statistics for a user\'s repositories and populate the information onto a GitHub static page',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=requirements,
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ]
)
