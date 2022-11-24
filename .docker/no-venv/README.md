The files here intend to rebuild and start the container without using Python virtual environments.
I HAVEN'T MANAGED TO MAKE THIS WORK!!

If you do not want to use venv in the containers, build with these lines uncommented/commented
dockerfile: .docker/no-venv/novenv.Dockerfile
#dockerfile: .docker/Dockerfile

If you want to use venv in the containers, build with these lines commented/uncommented
#dockerfile: .docker/no-venv/novenv.Dockerfile
dockerfile: .docker/Dockerfile