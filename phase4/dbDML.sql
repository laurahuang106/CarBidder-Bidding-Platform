# Initial data 

-- USERS Table
INSERT INTO USERS (user_id, user_type, user_name, email, balance, seller_rating, buyer_rating, num_of_seller_rating, num_of_buyer_rating, is_allowed_chat, is_allow_list) VALUES
(1, 'ADMIN', 'AdminOne', 'admin1@email.com', 40000.00, 0.00, 0.00, 0, 0, TRUE, TRUE),
(2, 'NORMAL_USER', 'MikeLee', 'mikelee@hotmail.com', 33000.00, 0.00, 0.00, 0, 0, TRUE, TRUE),
(3, 'NORMAL_USER', 'LucyWhite', 'lucywhite@gmail.com', 59000.00, 0.00, 0.00, 0, 0, TRUE, TRUE),
(4, 'NORMAL_USER', 'JohnSmith', 'johnsmith@yahoo.com', 19750.00, 0.00, 0.00, 0, 0, TRUE, TRUE),
(5, 'NORMAL_USER', 'EmmaBrown', 'emmabrown@aol.com', 9800.00, 0.00, 0.00, 0, 0, TRUE, TRUE),
(6, 'NORMAL_USER', 'OliviaJohnson', 'oliviaj@msn.com', 16000.00, 0.00, 0.00, 0, 0, TRUE, TRUE),
(7, 'NORMAL_USER', 'JamesWilliams', 'jamesw@gmail.com', 21750.00, 0.00, 0.00, 0, 0, TRUE, TRUE),
(8, 'NORMAL_USER', 'SophiaDavis', 'sophiad@outlook.com', 54300.00, 0.00, 0.00, 0, 0, TRUE, TRUE),
(9, 'NORMAL_USER', 'MichaelJordan', 'mjordan@nba.com', 90500.00, 0.00, 0.00, 0, 0, TRUE, TRUE),
(10, 'NORMAL_USER', 'SerenaWilliams', 'serenaw@tennispro.com', 32000.00, 0.00, 0.00, 0, 0, TRUE, TRUE),
(11, 'NORMAL_USER', 'LeoMessi', 'lmessi@footballstar.com', 35750.00, 0.00, 0.00, 0, 0, TRUE, TRUE);


-- LISTED_VEHICLES Table
-- 7 active listing and 7 inactive(sold) listing
INSERT INTO LISTED_VEHICLES (listing_id, vehicle_id, VIN, seller_id, image_url, vehicle_description, make, model, fuel_type, year_of_production, mileage, price, exterior_color, interior_color, state, zip_code, is_verified, listing_start_date, listing_end_date, listing_status) VALUES
(1, 1001, 'VIN000000000001', 2, 'http://example.com/car1.jpg', 'Good Condition', 'Toyota', 'Camry', 'Gas', 2019, 10000, 20000, 'Red', 'Black', 'CA', '90001', TRUE, '2023-01-01 10:00:00', '2023-01-10 10:00:00', FALSE),
(2, 1002, 'VIN000000000002', 3, 'http://example.com/car2.jpg', 'Almost New', 'Honda', 'Civic', 'Gas', 2021, 5000, 18000, 'Blue', 'Gray', 'TX', '75001', NULL, '2023-01-05 09:00:00', '2023-01-20 09:00:00', FALSE),
(3, 1003, 'VIN000000000003', 4, 'http://example.com/car3.jpg', 'Used', 'BMW', 'X3', 'Diesel', 2018, 15000, 30000, 'White', 'Black', 'NY', '10001', TRUE, '2023-01-07 08:00:00', '2023-01-30 08:00:00', FALSE),
(4, 1004, 'VIN000000000004', 5, 'http://example.com/car4.jpg', 'Old but gold', 'Mercedes', 'C-Class', 'Gas', 2016, 20000, 25000, 'Black', 'White', 'FL', '32004', NULL, '2023-01-10 07:00:00', '2023-01-25 07:00:00', TRUE),
(5, 1005, 'VIN000000000005', 6, 'http://example.com/car5.jpg', 'Reliable', 'Nissan', 'Altima', 'Gas', 2020, 7000, 18000, 'Silver', 'Gray', 'TX', '75003', TRUE, '2023-01-12 06:00:00', '2023-01-28 06:00:00', FALSE),
(6, 1006, 'VIN000000000006', 7, 'http://example.com/car6.jpg', 'Sporty', 'Ford', 'Mustang', 'Gas', 2019, 10000, 28000, 'Yellow', 'Black', 'NV', '89001', NULL, '2023-01-14 11:00:00', '2023-01-29 11:00:00', TRUE),
(7, 1007, 'VIN000000000007', 8, 'http://example.com/car7.jpg', 'Compact', 'Chevrolet', 'Spark', 'Gas', 2022, 2000, 14000, 'Green', 'Gray', 'WA', '98001', TRUE, '2023-01-15 10:00:00', '2023-01-31 10:00:00', FALSE),
(8, 1008, 'VIN000000000008', 9, 'http://example.com/car8.jpg', 'Sport Edition', 'Audi', 'A3', 'Gas', 2019, 8500, 27000, 'Gray', 'Black', 'IL', '60001', TRUE, '2023-02-01 10:00:00', '2023-02-15 10:00:00', FALSE),
(9, 1009, 'VIN000000000009', 9, 'http://example.com/car9.jpg', 'New Model', 'Volkswagen', 'Golf', 'Gas', 2022, 1000, 23000, 'Blue', 'Beige', 'NC', '28001', TRUE, '2023-02-03 09:00:00', '2023-02-18 09:00:00', FALSE),
(10, 1010, 'VIN000000000010', 10, 'http://example.com/car10.jpg', 'Economy Car', 'Hyundai', 'Elantra', 'Gas', 2021, 4500, 19000, 'White', 'Brown', 'TX', '76001', TRUE, '2023-02-05 08:00:00', '2023-02-20 08:00:00', TRUE),
(11, 1011, 'VIN000000000011', 10, 'http://example.com/car11.jpg', 'City Car', 'Kia', 'Rio', 'Gas', 2022, 2000, 17000, 'Black', 'Red', 'GA', '30001', TRUE, '2023-02-07 09:00:00', '2023-02-22 09:00:00', TRUE),
(12, 1012, 'VIN000000000012', 11, 'http://example.com/car12.jpg', 'Luxury SUV', 'Lexus', 'RX', 'Hybrid', 2018, 10000, 40000, 'Silver', 'Black', 'CA', '94001', TRUE, '2023-02-09 10:00:00', '2023-02-24 10:00:00', TRUE),
(13, 1013, 'VIN000000000013', 11, 'http://example.com/car13.jpg', 'Off-road', 'Jeep', 'Wrangler', 'Diesel', 2017, 12000, 32000, 'Green', 'Black', 'AZ', '85001', TRUE, '2023-02-11 11:00:00', '2023-02-26 11:00:00', TRUE),
(14, 1014, 'VIN000000000014', 5, 'http://example.com/car14.jpg', 'Electric Sedan', 'Tesla', 'Model 3', 'Electric', 2020, 8000, 35000, 'Red', 'White', 'OR', '97001', TRUE, '2023-02-13 12:00:00', '2023-02-28 12:00:00', TRUE);


-- BIDDINGS Table
INSERT INTO BIDDINGS (bidding_id, listing_id, user_id, bidding_amount, bidding_date, is_winner) VALUES
(1, 1, 4, 20250.00, '2023-01-02 11:00:00', TRUE),
(2, 2, 6, 18200.00, '2023-01-06 10:00:00', FALSE),
(3, 2, 6, 19000.00, '2023-01-07 11:00:00', TRUE),
(4, 3, 5, 30200.00, '2023-01-08 12:00:00', TRUE),
(5, 5, 7, 18250.00, '2023-01-13 13:00:00', TRUE),
(6, 5, 3, 14100.00, '2023-01-16 15:00:00', FALSE),
(7, 7, 3, 14300.00, '2023-01-18 19:00:00', TRUE),
(8, 8, 2, 27250.00, '2023-02-02 16:00:00', TRUE),
(9, 9, 6, 23250.00, '2023-02-04 17:00:00', TRUE),
(10, 4, 8, 25250.00, '2023-01-11 14:00:00', NULL),  
(11, 6, 9, 28500.00, '2023-01-15 14:00:00', NULL),
(12, 10, 3, 19300.00, '2023-02-06 18:00:00', NULL);


-- RATINGS Table
INSERT INTO RATINGS (rating_id, listing_id, seller_id, winner_id, seller_rate_from_winner, winner_rate_from_seller) VALUES
(1, 1, 2, 4, 4.8, 4.6),
(2, 2, 3, 6, 4.7, 4.3),
(3, 3, 4, 5, 4.6, 4.7),
(4, 5, 6, 7, 4.5, 4.8),
(5, 7, 8, 3, 4.8, 4.2),
(6, 8, 9, 2, 4.5, 4.5),
(7, 9, 9, 6, 4.2, 4.3);


-- VEHICLE_ORDERS Table
INSERT INTO VEHICLE_ORDERS (order_id, listing_id, buyer_id, seller_id, order_price, order_date, tracking_number, is_paid, is_shipped) VALUES
(1, 1, 4, 2, 20250.00, '2023-01-02 12:00:00', 10001, 1, 1),
(2, 2, 6, 3, 19000.00, '2023-01-07 12:00:00', 10002, 1, 1),
(3, 3, 5, 4, 30200.00, '2023-01-08 13:00:00', 10003, 1, 0),
(4, 5, 7, 6, 18250.00, '2023-01-13 14:00:00', 10004, 1, 0),
(5, 7, 3, 8, 14300.00, '2023-01-18 20:00:00', 10005, 1, 1),
(6, 8, 2, 9, 27250.00, '2023-02-02 17:00:00', 10006, 1, 0),
(7, 9, 6, 9, 23250.00, '2023-02-04 18:00:00', 10007, 1, 0);


-- CHATS Table
INSERT INTO CHATS (chat_id, sender_id, receiver_id, message, date, listing_id) VALUES
(1, 2, 3, 'Is the car still available?', '2023-01-02 12:30:00', 1),
(2, 3, 2, 'Yes, it is.', '2023-01-02 12:31:00', 1),
(3, 4, 3, 'Any damages?', '2023-01-06 13:10:00', 2),
(4, 3, 4, 'No damages. Almost new.', '2023-01-06 13:11:00', 2),
(5, 5, 4, 'Can I get a discount?', '2023-01-08 14:20:00', 3),
(6, 4, 5, 'Sorry, the price is fixed.', '2023-01-08 14:21:00', 3),
(7, 6, 5, 'Is the price negotiable?', '2023-01-11 15:30:00', 4),
(8, 5, 6, 'A little bit, but not much.', '2023-01-11 15:31:00', 4),
(9, 11, 3, 'Is the car still available?', '2023-01-02 12:30:00', 1),
(10, 3, 11, 'Yes, it is.', '2023-01-02 12:31:00', 1);


-- BALANCE_TRANSACTIONS Table
-- the inital balance amount of each users is 40000.00
-- current_balance is displayed as balance after the transaction is done
INSERT INTO BALANCE_TRANSACTIONS (transaction_id, user_id, current_balance, date, transaction_type, transaction_amount) VALUES
(1, 4, 19750.00, '2023-01-02 12:00:00', 'pay', 20250.00),
(2, 2, 60250.00, '2023-01-02 12:00:00', 'receive', 20250.00),
(3, 6, 21000.00, '2023-01-07 12:00:00', 'pay', 19000.00), 
(4, 3, 59000.00, '2023-01-07 12:00:00', 'receive', 19000.00), 
(5, 5, 9800.00, '2023-01-08 13:00:00', 'pay', 30200.00), 
(6, 4, 49950.00, '2023-01-08 13:00:00', 'receive', 30200.00),
(7, 7, 21750.00, '2023-01-13 14:00:00', 'pay', 18250.00),
(8, 6, 39250.00, '2023-01-13 14:00:00', 'receive', 18250.00),
(9, 3, 44700.00, '2023-01-18 20:00:00', 'pay', 14300.00), 
(10, 8, 54300.00, '2023-01-18 20:00:00', 'receive', 14300.00), 
(11, 2, 33000.00, '2023-02-02 17:00:00', 'pay', 27250.00), 
(12, 9, 67250.00, '2023-02-02 17:00:00', 'receive', 27250.00),
(13, 6, 16000.00, '2023-02-04 18:00:00', 'pay', 23250.00), 
(14, 9, 90500.00, '2023-02-04 18:00:00', 'receive', 23250.00),
(15, 10, 50000.00, '2023-02-05 11:00:00', 'pop_up', 10000.00),
(16, 11, 35000.00, '2023-02-07 09:00:00', 'withdraw', 5000.00);


-- VIOLATION_REPORTS Table
INSERT INTO VIOLATION_REPORTS (report_id, user_id, report_content) VALUES
(1, 2, 'This listing with VIN:VIN000000000001 seems to be vehicle.'),
(2, 3, 'This user "OliviaJohnson" has fake listings.'),
(3, 4, 'This user "OliviaJohnson"\'s car has hidden damages.'),
(4, 5, 'Spam messages from this user "JamesWilliams".'),
(5, 6, 'This user "JamesWilliams" never repsonses to chat.'),
(6, 7, 'Received a fake picture from this user "SophiaDavis".'),
(7, 8, 'This user "SophiaDavis" is not replying to any messages.'),
(8, 2, 'Suspicious activity on this user "SophiaDavis"\'s account.');


# Data Deletion: when a user cancels his/her bid on a listing
-- DELETE FROM BIDDINGS
-- WHERE user_id = 'selected_user_id' AND listing_id = 'selected_listing_id';

