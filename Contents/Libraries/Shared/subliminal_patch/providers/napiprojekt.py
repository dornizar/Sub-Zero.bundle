# coding=utf-8
import logging

from subliminal.providers.napiprojekt import NapiProjektProvider as _NapiProjektProvider, \
    NapiProjektSubtitle as _NapiProjektSubtitle, get_subhash
from subliminal_patch.extensions import provider_registry

logger = logging.getLogger(__name__)


class NapiProjektSubtitle(_NapiProjektSubtitle):
    def __init__(self, language, hash, fps):
        super(NapiProjektSubtitle, self).__init__(language, hash)
        self.release_info = hash
        self.plex_media_fps = float(fps)

    def __repr__(self):
        return '<%s %r [%s]>' % (
            self.__class__.__name__, self.release_info, self.language)


class NapiProjektProvider(_NapiProjektProvider):
    subtitle_class = NapiProjektSubtitle

    def query(self, language, hash, fps):
        params = {
            'v': 'dreambox',
            'kolejka': 'false',
            'nick': '',
            'pass': '',
            'napios': 'Linux',
            'l': language.alpha2.upper(),
            'f': hash,
            't': get_subhash(hash)}
        logger.info('Searching subtitle %r', params)
        response = self.session.get(self.server_url, params=params, timeout=10)
        response.raise_for_status()

        # handle subtitles not found and errors
        if response.content[:4] == b'NPc0':
            logger.debug('No subtitles found')
            return None

        subtitle = self.subtitle_class(language, hash, fps)
        subtitle.content = response.content
        logger.debug('Found subtitle %r', subtitle)

        return subtitle

    def list_subtitles(self, video, languages):
        return [s for s in [self.query(l, video.hashes['napiprojekt'], video.fps) for l in languages] if s is not None]


provider_registry.register("napiprojekt", NapiProjektProvider)
