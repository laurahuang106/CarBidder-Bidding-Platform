-- Drop tables if tables are exist
DROP TABLE IF EXISTS VIOLATION_REPORTS;
DROP TABLE IF EXISTS BALANCE_TRANSACTIONS;
DROP TABLE IF EXISTS CHATS;
DROP TABLE IF EXISTS VEHICLE_ORDERS;
DROP TABLE IF EXISTS RATINGS;
DROP TABLE IF EXISTS BIDDINGS;
DROP TABLE IF EXISTS LISTED_VEHICLES;
DROP TABLE IF EXISTS USERS;

-- Drop view if view are exist
DROP VIEW IF EXISTS Top10RatedSeller;

-- Drop function if tables are exist
DROP PROCEDURE IF EXISTS GetHighestBidDetails;
DROP procedure IF EXISTS GetHighestBid;
DROP procedure IF EXISTS UpdateExpiredListings;


-- Drop triggers if triggers are exist
DROP TRIGGER IF EXISTS update_user_ratings;

-- Drop EVENT if EVENT are exist
DROP EVENT IF EXISTS update_listing_status;