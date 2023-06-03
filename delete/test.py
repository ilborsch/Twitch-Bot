from environment.database import Session
from environment.database import engine
from environment.models import Channel
from src.utils import socials_to_list, socials_to_string
from environment.database import Base


from googletrans import Translator

translator = Translator()

# translate a spanish text to english text (by default)
translation = translator.translate('Success. Next step is to setup your bot.'
                               ' Use !setup_help command to get further information. ', dest="ru")
print(f"{translation.origin} ({translation.src}) --> {translation.text} ({translation.dest})")
