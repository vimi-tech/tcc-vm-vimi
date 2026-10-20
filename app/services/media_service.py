import os
import re
import uuid
from typing import List, Tuple
from werkzeug.utils import secure_filename

try:
    import cloudinary
    import cloudinary.uploader
except ImportError:
    cloudinary = None


class MediaService:
    """Serviço responsável pelo armazenamento e gerenciamento de arquivos de mídia (imagens e vídeos)."""

    EXTENSOES_PERMITIDAS = {
        '.jpg', '.jpeg', '.png', '.gif', '.webp',
        '.mp4', '.webm', '.mov',
    }

    def __init__(self, upload_folder: str = None):
        if upload_folder:
            self.upload_folder = upload_folder
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.upload_folder = os.path.join(base_dir, 'static', 'uploads')
        os.makedirs(self.upload_folder, exist_ok=True)

        self.cloudinary_ativo = self._configurar_cloudinary()

    def _configurar_cloudinary(self) -> bool:
        cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
        api_key = os.environ.get('CLOUDINARY_API_KEY')
        api_secret = os.environ.get('CLOUDINARY_API_SECRET')

        if cloudinary and cloud_name and api_key and api_secret:
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret,
                secure=True,
            )
            return True
        return False

    def salvar_midias(self, arquivos) -> Tuple[List[str], int]:
        """Processa e salva uma lista de arquivos de mídia. Retorna (lista_de_salvos, quantidade_ignorada)."""
        salvas = []
        ignoradas = 0

        if not arquivos:
            return salvas, ignoradas

        for arquivo in arquivos:
            if not arquivo or not getattr(arquivo, 'filename', None):
                continue

            base, extensao = os.path.splitext(arquivo.filename)
            extensao = extensao.lower()

            if extensao not in self.EXTENSOES_PERMITIDAS:
                ignoradas += 1
                continue

            base_segura = secure_filename(base) or 'midia'
            sufixo = f'{uuid.uuid4().hex[:8]}_{base_segura}'

            if self.cloudinary_ativo:
                try:
                    arquivo.stream.seek(0)
                    resultado = cloudinary.uploader.upload(
                        arquivo.stream,
                        resource_type='auto',
                        folder='feirascore',
                        public_id=sufixo,
                    )
                    salvas.append(resultado['secure_url'])
                except Exception as erro:
                    print('Erro ao enviar mídia para o Cloudinary:', erro)
                    ignoradas += 1
            else:
                nome_final = f'{sufixo}{extensao}'
                caminho_final = os.path.join(self.upload_folder, nome_final)
                arquivo.save(caminho_final)
                salvas.append(nome_final)

        return salvas, ignoradas

    def apagar_midia(self, nome_arquivo: str):
        """Apaga a mídia do Cloudinary ou do armazenamento local."""
        if not nome_arquivo:
            return

        if str(nome_arquivo).startswith(('http://', 'https://')):
            if self.cloudinary_ativo and 'res.cloudinary.com' in nome_arquivo:
                try:
                    tipo = 'video' if '/video/upload/' in nome_arquivo else 'image'
                    partes = nome_arquivo.split('/upload/', 1)[1].split('/')
                    if partes and re.fullmatch(r'v\d+', partes[0]):
                        partes = partes[1:]
                    public_id = os.path.splitext('/'.join(partes))[0]
                    cloudinary.uploader.destroy(public_id, resource_type=tipo)
                except Exception as erro:
                    print('Erro ao apagar mídia no Cloudinary:', erro)
            return

        caminho = os.path.join(self.upload_folder, nome_arquivo)
        if os.path.exists(caminho):
            try:
                os.remove(caminho)
            except OSError as erro:
                print('Erro ao remover arquivo local:', erro)
