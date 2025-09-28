from setuptools import setup, find_packages


# Function to read requirements from requirements.txt
def read_requirements(filename="requirements.txt"):
    with open(filename, "r") as f:
        # Use .strip() to remove whitespace/newlines,
        # and filter out empty lines or comments (starting with #)
        return [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]


setup(
    name="api",
    version="1.0",
    description="A whatsapp bot that sends baller of the day information",
    author="Simão Gonçalves",
    author_email="simao.campos.goncalves@gmail.com",
    packages=find_packages(),
    install_requires=read_requirements(),
    #     "wheel",
    #     "bar",
    #     "greek",
    # ],  # external packages as dependencies
)
