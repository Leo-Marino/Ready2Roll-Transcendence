from urllib.parse import quote

from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    """
    Come lo storage S3/MinIO normale, ma gli URL dei file sono RELATIVI: /media/<percorso>.

    Il browser li richiede allo stesso indirizzo da cui ha aperto il sito (nginx, porta 8080),
    e nginx li inoltra a MinIO. Cosi' non serve conoscere l'IP del server.
    """

    def url(self, name, *args, **kwargs):
        return '/media/' + quote(str(name).lstrip('/'))
