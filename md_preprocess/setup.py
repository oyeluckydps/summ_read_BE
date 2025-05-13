"""
Setup script for MD Preprocess library.
"""

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    # LATER: Ignore the personal details as of now.
    name='md_preprocess',
    version='0.1.0',
    description='A library for preprocessing markdown files extracted from PDFs using LLMs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/md_preprocess',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.8',
    install_requires=[
        'anthropic>=0.5.0',
    ],
    entry_points={
        'console_scripts': [
            'md_preprocess=md_preprocess.cli:main',
        ],
    },
)