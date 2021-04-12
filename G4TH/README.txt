################
SET UP GUIDE
################

1. Go into the G4TH_app folder, and then go into the setup folder.

2. Copy load.sql onto your MySQL workbench / PHPmyadmin and upload the databases and sample databases

3. Run the docker-compose file to build all images and start all containers.

4. Go to http://localhost:1337/register to register an admin account on Konga

5. Create a new connection and fill in using the following details:

Name: G4TH
Kong Admin URL: http://kong:8001/

6. Activate the connection.

7. Go to "Snapshots", click "Import From File" and select the kong.json file that is in the setup folder.

8. Click on "Details" and click on "Restore". Tick "services" and "routes" and click "Import Objects".

9. Your Konga is all set! Now, go to "UI Screens" folder and open dashboard.html on your browser.

10. You can now start navigating around the UI

###########################
TESTING ON DIFFERENT USERS
###########################

In order to switch users, you have to change the value of the hidden input type to the username you wish to login as for EACH PAGE manually.
These input types are labelled with comments "TEMP STORAGE FOR USER" on the HTML file.

e.g. of a section of code in the HTML file:
<!-- TEMP STORAGE FOR USER-->
    <input type='hidden' id='current' value='Michelle'>
<!-- TEMP STORAGE FOR USER-->

As shown, the user is currently logged into as Michelle. In order to login as Meghan, the value must be replaced with 'Meghan'.

You can use the following usernames to test:

- Sarah Baumert (MEMBER)
- Michelle
- Meghan
- Christine
- Mieka
- Lunatone
- Torrence
- Monique
- Yuri
- Alison
- Chrissa
- Meese
- Gina Poskitt (MEMBER)

################
ADDITIONAL NOTES
################

1. In User's Inventory, the Redeem function is only for display; it does not work.
2. The Logout button in the Navbar does not work, it is only for display to simulate an already-logged in user.