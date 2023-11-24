from setuptools import setup, find_packages

setup(
    name='ndax_trader',  # This should be your package name.
    version='0.1.0',  # Start with a small version number for an initial release.
    author='Cédric Lam',  # Replace with your name.
    author_email='ced29lam@gmail.com',  # Replace with your email.
    description='A Python wrapper for the NDAX cryptocurrency exchange API.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/tailinks/ndax_trader',  # Replace with the URL to your repository.
    packages=find_packages(),
    install_requires=[
        'pandas',
        'websocket-client',
        'python-dotenv',
        'pyotp',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',  # Change as appropriate for your package maturity.
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',  # Specify the compatible Python versions.
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.6',  # Specify the minimum Python version required.
    keywords='ndax, cryptocurrency, trading, api, websocket',  # Add keywords relevant to your package.
)
