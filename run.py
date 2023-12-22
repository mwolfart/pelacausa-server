from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class MyHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            return
        if event.event_type in ['modified', 'created']:
            print(f'Rebuilding and restarting the container...')
            subprocess.run(['docker-compose', 'up', '--build', '-d', '--force-recreate'])

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(MyHandler(), path='.', recursive=True)
    observer.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
