import docker
import dockerpty

client = docker.Client()

print("Creating container...")
container = client.create_container(
    image='busybox:latest',
    command='/bin/sh',
    stdin_open=True,
    tty=True,
)

try:
    print("Starting container...")
    client.start(container)
    dockerpty.PseudoTerminal(client, container).start()
    client.wait(container)
finally:
    print("Cleaning up...")
    try:
        client.kill(container)
    except:
        pass
    client.remove_container(container)
