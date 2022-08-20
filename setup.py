from os import path

from setuptools import setup, find_packages

desc_file = "README.md"

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, desc_file), encoding="utf-8") as f:
    long_description = f.read()

print(long_description)

# get the dependencies and installs
with open(path.join(here, "requirements.txt"), encoding="utf-8") as f:
    all_reqs = f.read().split("\n")

install_requires = [x.strip() for x in all_reqs if "git+" not in x]
dependency_links = [
    x.strip().replace("git+", "") for x in all_reqs if x.startswith("git+")
]

setup(
    name="fastapi-authz",
    description="An authorization middleware for FastAPI that supports ACL, RBAC, ABAC, based on PyCasbin",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Zxilly",
    author_email="zhouxinyu1001@gmail.com",
    url="https://github.com/pycasbin/fastapi-authz",
    license="Apache 2.0",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    keywords=[
        "fastapi",
        "starlette",
        "middleware",
        "pycasbin",
        "casbin",
        "auth",
        "authz",
        "acl",
        "rbac",
        "abac",
        "access control",
        "authorization",
        "permission"
    ],
    packages=find_packages(exclude=["docs", "test*"]),
    data_files=[desc_file, "requirements.txt"],
    include_package_data=True,
    install_requires=install_requires,
    dependency_links=dependency_links
)
