This is a group project from CSE 312 Web application charged by Jesse.
The group meeting is scheduled every Wednesday 5:00pm - 7:00pm at Group Study Room in Silverman Library.

Project Link: https://cse312.ubcs.top:19550/
Backup Link: https://cse312.ubcs.us.kg/
_______________________________________________________________________________________________________
____________________________Project Part 3 Objective 3: Following&Followers____________________________

Testing Procedure:
1. Register and Login as a user.
2. Repeat step 1 again in another browser.
3. Open Developer Tool in both browser.
4. Create a post and refresh the web page to see follow button.
5. Try to follow a user using the Follow Button aside the user avatar
    -In Network tab, see if there is a Post method with 200 status. Under the Network - Response - you should see JSON success: true. [the file name should as same as the USERNAME as you followed]
    -Refresh the page to see if the change is made.
    -Likewise, unfollowed the user and see if there is a Post method with 200 status. Under the Network - Response - you should see JSON success: true. [the file name should as same as the USERNAME as you followed]
    -Refresh the page again to see changes.
6. In the right top corner, you should find following and followers.
7. Open followers.
    -Repeat Step 5, you should see changes after you refresh the page. NOTE: Repeat without seeing the Network tab, you won't see any status updated here.
8. Go back to the home page.
    -Follow several users you like.
    -Open following.
        -You should be able to see list of users you subscribed.
_______________________________________________________________________________________________________

USE pip install flask TO INSTALL FLASK
#### While you have something updated file want to upload to this project, make sure create and upload it to your own branch first. Make a pull request and we will merge it to the main branch if and only if we all together test.
#Please add your commit description below before next meeting, so that other member can understand what changes you have made.

Project Logs:
10/22/2024 Zijun Wei: Modified Login/Register.html. Partially implemented Login/Register (BUGs exist, but fixed by other teammate.)
10/03/2024 Zijun Wei: Rebuild static folder. Modified app.py. Now each file has correct mime type and nosniff

10/03/2024 Zijun Wei: Modified index html so that post container can automatically adjust size fits to contents. modified index.css. created 404 html. uploaded flower image. Fixed a bug in docker-compose.yml. Modified app.py so that the web now can correctly return 404 page when Page not found.

10/02/2024 Zijun Wei: Re structure the project. templates folder holds html files and static folder stores CSS and JavaScript files. Modified index.html and index.js so that when user click on the user/login icon, chat.js will redirect user to login page. Modified app.py, pages can correctly display on the localhost now.

10/01/2024 Zijun Wei: Created README.md. Create a folder named util that consists of chat/post html, CSS, and JavaScript files. Dockerfile and docker-compose.yml are temporarily set up and ready to go. requirements.txt is created, yet it only contains pymongo and Flask. chat/post html file is implemented. chat/post CSS is partially implemented. chat/post JavaScript is not implement now.


