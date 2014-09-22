# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as bs
import subprocess as sub
import math
import os
import sys

storyboard = sys.argv[1]
android = sys.argv[2]

package = "com.cosmicbyte.demo"
appname = "Demo App"

class Frame:
	def __init__(self, x, y, width, height):
		self.x = int(float(x) * 1.125)
		self.y = int(float(y) * 0.99647887323944)
		self.width = int(float(width) * 1.125)
		self.height = int(float(height) * 0.99647887323944)

class Color:
	def __init__(self, red, green, blue):
		self.red = float(red) * 255
		self.green = float(green) * 255
		self.blue = float(blue) * 255
		self.hex = '#ff%02x%02x%02x' % (self.red, self.green, self.blue)

class Button:
	def __init__(self, id, text, frame):
		self.id = id
		self.text = text
		self.frame = frame

class ImageButton:
	def __init__(self, id, image, imagePressed, frame):
		self.id = id
		self.image = image
		self.imagePressed = imagePressed
		self.frame = frame

class TextView:
	def __init__(self, text, color, size, alignment, frame):
		self.text = text
		self.color = color
		self.size = int(size) - 1
		self.alignment = alignment
		self.frame = frame

class Switch:
	def __init__(self, on, frame):
		self.on = str(on).lower()
		self.frame = frame

class SeekBar:
	def __init__(self, min, max, value, frame):
		self.max = int(max - min)
		self.value = value - min
		self.frame = frame

class ImageView:
	def __init__(self, image, frame):
		self.image = image
		self.frame = frame


imageButtons = []

soup = bs(open(storyboard), "xml")
count = 1
buttoncount = 1
for scene in soup.find_all("scene"):
	views = []
	segues = []

	if scene.objects.navigationController is None:
		for view in scene.objects.viewController.view.subviews.findChildren(recursive=False):
			type = view.name
			rect = view.rect
			frame = Frame(rect['x'], rect['y'], rect['width'], rect['height'])
			
			if type == "button":
				if view.has_attr('buttonType'):
					if view['buttonType'] == 'infoLight':
						views.append(ImageButton("@+id/button" + str(buttoncount), "ic_menu_info_details", "ic_menu_info_details", frame))
					else:
						views.append(Button("@+id/button" + str(buttoncount), view.state['title'], frame))
				else:
					views.append(ImageButton("@+id/button" + str(buttoncount), view.find(key='normal')['image'], view.find(key='normal')['image'], frame))

				try:
					scenecount = 1
					dest = view.connections.segue['destination']
					imageButtons.append(dest)
					for scene in soup.find_all('scene'):
						vcid = scene.objects.viewController['id']
						if dest == vcid:
							segues.append([buttoncount, count, scenecount])
						scenecount += 1
				except:
					pass

				buttoncount += 1
			elif type == "imageView":
				views.append(ImageView(view['image'], frame))
			elif type == "label":
				alignment = 'left'
				if view.has_attr('textAlignment'):
					alignment = view['textAlignment']
				size = view.fontDescription['pointSize']
				if not view.color.has_attr('cocoaTouchSystemColor'):
					color = Color(view.color['red'], view.color['green'], view.color['blue'])
					views.append(TextView(view['text'], color, size, alignment, frame))
				else:
					views.append(TextView(view['text'], Color(0, 0, 0), size, alignment, frame))
			elif type == "slider":
				views.append(SeekBar(float(view['minValue']), float(view['maxValue']), float(view['value']), frame))
			elif type == "switch":
				on = view['on'] == "YES" if True else False
				views.append(Switch(on, frame))

	newsoup = bs(features='xml')

	layout = newsoup.new_tag('RelativeLayout')
	layout['xmlns:android'] = "http://schemas.android.com/apk/res/android"
	layout['xmlns:tools'] = "http://schemas.android.com/tools"
	layout['android:layout_width'] = "match_parent"
	layout['android:layout_height'] = "match_parent"
	layout['android:paddingLeft'] = "0dp"
	layout['android:paddingRight'] = "0dp"
	layout['android:paddingTop'] = "0dp"
	layout['android:paddingBottom'] = "0dp"
	layout['tools:context'] = ".Activity" + str(count)

	for view in views:
		name = view.__class__.__name__
		tag = newsoup.new_tag(name)
		tag['android:layout_width'] = str(view.frame.width) + 'dp'
		tag['android:layout_height'] = str(view.frame.height) + 'dp'
		tag['android:layout_marginTop'] = str(view.frame.y) + 'dp'
		tag['android:layout_marginLeft'] = str(view.frame.x) + 'dp'

		if name == 'Button':
			tag['android:text'] = view.text
			tag['android:padding'] = "0dp"
			tag['android:id'] = view.id
		elif name == 'ImageButton':
			if ".png" in view.image:
				os.system("cp '" + storyboard.replace("Base.lproj/Main.storyboard", "") + view.image + "' '" + android + "app/src/main/res/drawable-xxhdpi/" + view.image.replace('-', '_') + "'")
				os.system("cp '" + storyboard.replace("Base.lproj/Main.storyboard", "") + view.imagePressed + "' '" + android + "app/src/main/res/drawable-xxhdpi/" + view.imagePressed.replace('-', '_') + "'")
				tag['android:id'] = view.id
				tag['android:background'] = '@drawable/' + view.image.replace('.png', '').replace('-', '_')
			else:
				tag['android:id'] = view.id
				tag['android:background'] = '@drawable/' + view.image
		elif name == 'ImageView':
			os.system("cp '" + storyboard.replace("Base.lproj/Main.storyboard", "") + view.image + "' '" + android + "app/src/main/res/drawable-xxhdpi/" + view.image.replace('-', '_') + "'")
			tag['android:src'] = '@drawable/' + view.image.replace('.png', '').replace('-', '_')
		if name == 'SeekBar':
			tag['android:max'] = view.max
			tag['android:value'] = view.value
		elif name == 'Switch':
			tag['android:checked'] = view.on
		elif name == 'TextView':
			tag['android:text'] = view.text
			tag['android:textColor'] = view.color.hex
			tag['android:textSize'] = str(view.size) + 'dp'
			tag['android:gravity'] = view.alignment

		layout.append(tag)
	newsoup.append(layout)

	with open(android + "app/src/main/res/layout/activity" + str(count) + ".xml", 'w+') as f:
		f.write(newsoup.prettify())

	with open(android + "app/src/main/java/com/cosmicbyte/demo/Activity" + str(count) + ".java", 'w+') as f:
		segueexists = False
		seguestring = ""
		for segue in segues:
			if segue[1] == count:
				seguestring += "handleButton(R.id.button" + str(segue[0]) + ", new Intent(Activity" + str(count) + ".this, Activity" + str(segue[2]) + ".class));\n"
				f.write("package " + package + """;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.ImageButton;

public class Activity""" + str(count) + """ extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity""" + str(count) + """);

        """ + seguestring + """
    }

    private void handleButton(int id, final Intent intent) {
        if (findViewById(id) instanceof Button) {
            Button button = (Button) findViewById(id);
            button.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    startActivity(intent);
                }
            });
        } else {
            ImageButton button = (ImageButton) findViewById(id);
            button.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    startActivity(intent);
                }
            });
        }
    }
}""")
			segueexists = True
		if not segueexists:
			f.write("package " + package + """;

import android.app.Activity;
import android.os.Bundle;

public class Activity""" + str(count) + """ extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity""" + str(count) + """);
    }
}""",)

	androidsoup = bs(open(android + "app/src/main/AndroidManifest.xml", 'r'), 'xml')
	manifest = androidsoup.find('manifest')
	application = androidsoup.find('application')
	activity = androidsoup.new_tag('activity')
	activity['android:name'] = ".Activity" + str(count)
	activity['android:label'] = appname
	if len(application.findChildren()) == 0:
		intent_filter = androidsoup.new_tag('intent-filter')
		action = androidsoup.new_tag('action')
		action['android:name'] = "android.intent.action.MAIN"
		category = androidsoup.new_tag('category')
		category['android:name'] = "android.intent.category.LAUNCHER"
		intent_filter.append(action)
		intent_filter.append(category)
		activity.append(intent_filter)
	application.append(activity)

	with open(android + "app/src/main/AndroidManifest.xml", 'w+') as f:
		f.write(androidsoup.prettify())

	print("Finished converting view " + str(count))

	count += 1