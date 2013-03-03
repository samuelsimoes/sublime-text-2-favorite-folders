#Sublime Text 2 Favorite Folders Navigator

*[WIP]*

Plugin to help you navigate through the favorite folders on your project, you can also exclude, create, rename and move folders and files.

In projects using Magento or something like, for example, this can be very useful once the file working tree is giant and many folders has the same name, but in differents places.

!['Bookmakerd Folders List'](https://photos-1.dropbox.com/t/0/AAANl2_2n20EenwAa_-TKEo1vAtLB_LXfS_3P-FrVi8epw/12/29410635/png/2048x1536/2/1362330000/0/2/list_favorite_folders.png/gopojCbjZoehI-eDjjrJLmoPX63kyxN5gUthycoQssg)

!['Bookmakerd Folders List'](https://photos-6.dropbox.com/t/0/AAD1s9aVQ8tJS-IlcZ9Ed-a71yQTw-xnWnV-pL4sscT1cQ/12/29410635/png/1024x768/2/1362330000/0/2/list_edit.png/KP7oXAMD1bvMAYhGdp7DKPQ3Tfc3Di7m2-hxuApVyk4)

You need declare in to .sublime-project wich folders you want be bookmarked inside an array with key "folders", the three items should follow the format: **["Absolute Path to Folder", "Title of Bookmark", "Description of Bookmarked Folder"]**

You can set a regular expression to filter folders setting the key **excluded_dir_patterns**

**.sublime-project example**

```json
{
	"folders": [
		{
			"path": "/Users/samuel/magento_project"
		}
	],
	"settings":
	{
		"FavoriteFolders":
		{
     		"excluded_dir_patterns": ".git|.sass-cache|.DS_Store",
			"folders": [
				["/Users/samuel/magento_project/app/design/frontend/default/my_teme", "My Themes Files", "Files of my theme, lol"],
				["/Users/samuel/magento_project/skin/frontend/default/sprint", "My Themes Assets", "Assets of my Theme"]
			]
		}
	}
}
```