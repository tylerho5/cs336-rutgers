For this project we will be taking the database created in project 0 and converting it into a fully normalized database.

Step 1
-----
Using the names of columns, write down all functional dependencies you observe in the data.
You only need to write the cannonical cover.

Lastly, write down the normalized relations you are intending to create. Each relation should be in 3rd normal form. Each decomposition should be lossless and dependency preserving. 

For formatting you can just use sets of column names for example:

Location(blah, blue, color) for the location relation (do not change any of the column names).

{blah} -> {Blue, color} For a functional dependency

TO TURN IN:
A pdf document showing the functional dependencies and the final normalized relations. 


Step 2
----------
You should then write an SQL script that creates tables, and takes this data and divides it into those tables to reduce the functional dependencies. The final table should also be in 1st normal form, meaning columns like appicant_race_2 should not exist. You can add any additional attibutes needed to put it in 1st normal form as long as you are adding fewer attributes than you are removing. 

In addition to normalization, you need to give each column the appropriate type and foreign key status. This means the only columns which should remain text are columns which have no better datatype. Cells which only contain the empty string should be changed to contain NULL.

I recommend you retain the script which creates the preliminary table from the previos project as a seperate script so you don't need to rerun it every time.

You will then need to normalize the data. Specifically it must be in at least 3rd normal form, and preserve functional dependancies, and lossless decomposition. To decide which tables to use, you can start with your previos ER diagram as a guide. All data in the origional file will need to be recoverable from your final database, but data redundency should be limited by using 3NF. There is no need to create unneccecary tables, only create the tables neeeded to go into 3rd normal form.

You will need to create several new primary keys, you will need one for the application as a whole (in other words every row needs a new unique number to identify it and act as primary key) since there is no key in the original CSV. This should already be done from the previos project. You will also need a primary key for location, since no one column determines all location information. These can be any serial numbers, but should be unique to the location. These are the only two columns you should create after the initial normalization into 1st normal form.

Figuring out how to deal with location is probably the most difficult part of this project you may find the concat function helpful (though there are definitely many other ways to solve this problem). 

For the purpose of this problem assume that the entire relation is the only candidate key. In other words:The following columns relate to location (together) form a composite key that uniqly determine a location: 

county_code, msamd, state_code, census_tract_number, population ,minority_population,hud_median_family_income,tract_to_msamd_income,number_of_owner_occupied_units,number_of_1_to_4_family_units

You must create a simple integer primary key for each location, that key should be the only location information in the main application table.

columns such as applicant_race_1, applicant_race_2, applicant_race_3 etc. should not appear in any normalized table. Instead there should be a join table with, for example, 3 columns one for application_id one for race and one for race number. If only application race 1 is non-null this table will have only one row for with that application_id, and the last column would be 1. If both applicant_race_1 and applicant_race_2 are non-null then there will be 2 rows, one with the last column as 1 and one with the last column as 2. This is part of the initial normalization into 1st normal form.

---hints---
The columns which are completly null all the way through (such as Edit Status) can all be stored in a single table that will have only one row with all nulls, this will be useful for recreating the csv at the end. 

Columns with the word "name" are usually functionally dependent on a similar column which gives the code. There should be a table mapping codes to names, and the main table should only include the codes. https://files.consumerfinance.gov/hmda-historic-data-dictionaries/lar_record_codes.pdf is very helpfull in figuring out how to do this. Though if there is a conflict between this site and the way the data is actually represented in the CSV follow the CSV.

NO feild should have a text type in the main application table except perhaps respondent_id, they should all be numeric or one of the int datatypes. The text feilds should be relegated to the secondary tables. For example, loan_type should apear in the main table as an int or smallint, and there should be a secondary table that connects it to loan_type_name.

For now, the "State" table will have only one row, the one for NJ, but should still include the name and abreviation.  

TO TURN IN:
1. The preliminary script from the last project.
2. The complete SQL script that creates the normalized database from the prelinary table
3. A video
   The video should show you running the SELECT * FROM TABLE; for each new table replace TABLE with the name of each of your new normalized tables. You may show only the first part of each table after which you can use q to exit. You can also include these commands in a script in order to run them faster in a video, showing only the output tables.

Error Checking and Report generation
-----------

NOTHING THE USER CAN DO SHOULD EVER PUT THE DATABASE IN AN INCOSISTANT STATE, they should get an immediate rejection if they, for example, try to select a code of 4 for property type. This can be done with foreign keys

You should use the given CSV to figure out which columns can be null and which cannot. Assume that any column that is never null in the real data can never be null.


Lastly, write a single SQL command that rejoins all the tables and writes it out to a CSV. This CSV should be exactly identical to the origional CSV we started with. This command should only access the normalized tables and by this point the origional table should be deleted.

TO TURN IN:
1. An SQL script which takes your normalized database and puts it into a CSV
2. A video showing the incorrect attempts 
   Your video should show an attempt to run 3 incorrect insertion commands which the database rejects, it should show at least 3 different attempts rejected for different reasons
   we may try a different incorrect attempt in addition to watching your video.
   NOTE: we may try a different incorrect attempt in addition to watching your video.
2. A video showing you recreating the CSV. The video should show you running the code and opening the generated CSV in a spreadsheet program and scrolling to show all columns.

------


Academic Dishonesty
------------------

Code coppied from anywhere will be dealt with according to the Rutgers Academic Dishonesty policy.
If the copied code's source is referenced, the maximum penalty will be 75% off the given assingment, 
and likely nothing depending on how much was copied and whether you had the license.

It is OK to take code from official language documentation, but you should still cite it.

AI is not permitted for this assingment, and will be treated the same way as any other code from an outside source

If the code is not cited, and makes up a substantial portion of the project, the MINIMUM penalty will be
a zero on the assignment.


README file
-----------


You must also submit a README file (named README.txt) with clearly
delineated sections for the following. 

0. Please write down the full names and netids of both your team members.
1. Are there known issues or functions that aren't working currently in your
   attached code? If so, explain. (note that you will get half credit for any reasonably sized bug that is fully explained in the readme)
2. Collaboration: Who did you collaborate with on this project? What resources and refer-
ences did you consult? Please also specify on what aspect of the project you collaborated or
consulted.

3.What are some interesting questions about mortgages in NJ your database can answer?

4. What problems did you face developing code for this project? Around how long did you spend on this project (This helps me decide what I need to explain more clearly for the next projects)

5. If you prefer, you can turn in your videos here as links instead of uploading them to canvas. These links must remain live until you recieve your final grade in this course, and should include some dating indication such as upload date to show they were done before the deadline.

Submission
----------


Turn in your project on Canvas assignments. Only one team member should submit. 
Please submit your final project as a single zip file with the exact following files inside it
 (the readme should be a txt file)(Note caps in file and folder names).

- All scripts listed under each part
- The PDF from step 1 showing your Functional dependencies and normalized relations.
- The README
- The videos (Unless the vidoes are linked in the readme)