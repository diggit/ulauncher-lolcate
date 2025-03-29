from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenAction import OpenAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.event import PreferencesEvent
from ulauncher.api.shared.event import PreferencesUpdateEvent
from ulauncher.api.shared.event import ItemEnterEvent
from locator import Locator

import logging

logger = logging.getLogger(__name__)

locator = Locator(logger)

class Config:
	limit = 5

class SearchFileExtension(Extension):
	def __init__(self):
		super(SearchFileExtension, self).__init__()
		self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
		self.subscribe(PreferencesEvent, PreferencesEventListener())
		self.subscribe(PreferencesUpdateEvent, PreferencesUpdateEventListener())
		self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class PreferencesUpdateEventListener(EventListener):
	def on_event(self, event, extension):
		if event.id == 'limit':
			Config.limit = int(event.new_value)


class PreferencesEventListener(EventListener):
	def on_event(self, event, extension):
		Config.limit = int(event.preferences['limit'])


class ItemEnterEventListener(EventListener):
	def on_event(self, event, extension):
		results = event.get_data()
		items = []
		for file in results:
			items.append(ExtensionSmallResultItem(icon='images/copy.png',
				name = file,
				on_enter = CopyToClipboardAction(file)))
		return RenderResultListAction(items)


class KeywordQueryEventListener(EventListener):
	def __lolcateNotFound(self) -> list[ExtensionResultItem]:
		items = []
		items.append(ExtensionResultItem(icon='images/error.png',
									name="no lolcate executable",
									description="missing or not in PATH",
									on_enter=OpenUrlAction("https://github.com/ngirard/lolcate-rs")
									))
		return items
	
	def __noArgs(self):
		items = []
		items.append(ExtensionResultItem(icon='images/info.png',
									name="update default database",
									description="re-index default database, may take time",
									on_enter=RunScriptAction("lolcate --update")
									))
		return items
				
	def on_event(self, event, extension) -> RenderResultListAction:
		arg = event.get_argument()
		items = []

		if not locator.has_lolcate():
			logger.info("lolcate missing!")
			return RenderResultListAction(self.__lolcateNotFound())	
		if arg is None:
			logger.info("no args provided")
			items = self.__noArgs()
			pass
		else:
			try:
				results = locator.run(arg)
				totalMatches = len(results)
				logger.debug(f"assembling {min(Config.limit, totalMatches)} results")
				for match in results[:Config.limit]:
					logger.debug(f"match: {match}")
					items.append(ExtensionResultItem(icon='images/ok.png',
						name = match.split("/")[-1], #only file/dir name
						description = match, # full path
						on_enter = OpenAction(match),
						on_alt_enter = CopyToClipboardAction(match)))
				if totalMatches > Config.limit:
					extra = totalMatches - Config.limit
					logger.info(f"showing {totalMatches}, another {extra} matches hidden")
					items.append(ExtensionSmallResultItem(
						icon='images/info.png',
						name = f"...and {extra} more matches",
						highlightable = False)) # TODO: add option to load more results
			except Exception as e:
				error_info = str(e)
				items = [ExtensionSmallResultItem(icon='images/error.png',
												name = error_info,
												on_enter = CopyToClipboardAction(error_info))]
		
		return RenderResultListAction(items)


if __name__ == '__main__':
	SearchFileExtension().run()
