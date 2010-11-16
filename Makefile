all: ui_multiqml.py multiqml_ru.qm resources.py

resources.py: resources.qrc
	pyrcc4 resources.qrc -o resources.py

multiqml_ru.qm: translations/multiqml_ru.ts 
	pylupdate4 __init__.py plugin.py multiqml.py ui_multiqml.py -ts translations/multiqml_ru.ts
	lrelease translations/multiqml_ru.ts -qm translations/multiqml_ru.qm

ui_multiqml.py: multiqml.ui
	pyuic4 -o ui_multiqml.py multiqml.ui

clean:
	rm -f ui_multiqml.py translations/multiqml_ru.qm resources.py
