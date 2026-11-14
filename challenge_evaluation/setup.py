import os
from glob import glob

from setuptools import setup

package_name = 'challenge_evaluation'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.xml')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'config'), glob('config/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='root@todo.todo',
    description='Package to evaluate solutions for the robotics challenge',
    license='TODO',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'evaluation = challenge_evaluation.evaluation:main',
        ],
    },
)
