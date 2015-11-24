# Directions
These steps will explain how to deploy the CE 186 Nano DB to Heroku without installing anything on your laptop.

### Create Accounts
- Setup a [Heroku] account. It's free. 
- Setup a [Cloud9]. It's free. We will use Cloud9 to edit and deploy the app.

### Clone The App
 - Create a new work station on Cloud9 (c9.io) and use the Custom template.This will take a minute as Cloud9 creates a virtual machine.
 - Use the console at the bottom of the page to clone the app into your work station.
 - Note: Only enter the text that comes after $.
 - Note: /nano-db-for-heroku $ means you must run the command from the nano-db-for-heroku directory.
```sh
$ git clone https://github.com/ericburger/nano-db-for-heroku
```
 - You now have your own copy of the Nano DB server which you can edit from the Cloud9 work station.
 
### Connect To Heroku
 - Next we will login to Heroku from Cloud9.
```sh
$ heroku login
```

### Create a New Heroku App with a PostreSQL Database
```sh
$ cd nano-db-for-heroku/
/nano-db-for-heroku $ heroku create
/nano-db-for-heroku $ heroku addons:create heroku-postgresql:hobby-dev
```

### Create a Git Repository
 - This step is unnecessary but I've included it for completeness.
```sh
/nano-db-for-heroku $ git init
/nano-db-for-heroku $ git add --all
/nano-db-for-heroku $ git commit -m "Initial Save"
```

### Deploy the App
```sh
/nano-db-for-heroku $ git push heroku master
```
 - That is it. The Nano DB is now running on Heroku. Below are a few more notes. 
 
### Run from Cloud9
 - I recommend testing your app on your laptop and then only using Cloud9 to send changes to Heroku. In my experience, the connection between Cloud9 and the Heroku PostgreSQL database is really slow. Nonetheless, if you really want to test the app from Cloud9...
 - If you have not already done so, install the necessary Python modules.
```sh
$ pip install Flask gunicorn psycopg2
```
 - To run the app from Cloud9, login to Heroku from the Cloud9 console and run
```sh
/nano-db-for-heroku $ DATABASE_URL=$(heroku config:get DATABASE_URL) heroku local
```
 - The app will be running at https://WORKSPACE-USERNAME.c9users.io/ where WORKSPACE is the name of your workspace and USERNAME is your Cloud9 username. Use CTRL+C to close the app. 
 
### Forgetful Nano DB
 - The Heroku PostgreSQL Hobby database has a limit of 10,000 rows (effectively, 10,000 datapoints). Instead of using PostreSQL, The Nano DB server can be set to use an SQLite database instead. However, when running on Heroku, all the data will get deleted every 24 hours. For many of you, however, this is not a problem. This will also allow you to test the server directly from Cloud9. 
 - To change from using PostreSQL to SQLite, open the nanodb.py file. Near the top of the file, change 'type':'PostgreSQL' to 'type':'SQLite'. 
 - Now, to run the app from Cloud9, open the nanoserver.py file and click the green run button at the top of the page.
 
 
 
### Saving Changes and Pushing to Heroku
 - After making changes to your app, enter these commands to push the changes to Heroku.
```sh
$ cd nano-db-for-heroku/
/nano-db-for-heroku $ git add --all
/nano-db-for-heroku $ git commit -m "Message Describing Changes"
/nano-db-for-heroku $ git push heroku master
```


   [Heroku]: <https://www.heroku.com/>
   [Cloud9]: <https://www.c9.io/>


