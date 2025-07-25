# TODO

- [ ] Solve the remove_question problems
    - [X] make the file
    - [ ] Test it
- [X] tests for insert_user_by_name and replace insert_user
- [X] implement update database
    - update questions
    - if a question is solved update all its responses and transactions and update users stats
    - notify of new stats of users 
- [x] implement betting system
    - [x] print user stats
        - [x] prediction stats
        - [ ] financial stats
            - [ ] liquid budget vs full budget (liquid + \sum price_i stake_i) and table for each market
    - [ ] remember what price stock was bought, so i know after multiple update database, what the full net profit was 
    - [x] cli
        - [x] transaction prompt
            - [x] main functionailty
            - [x] better prints
        - [x] portfolio choice to sell
            - [ ] prompt to sell all stake for market (a) 
    - [x] perform transaction
    - [x] update database
        - [x] inform users of stock change upon updating
        - [X] automatic stock sells upon market completion   
- [ ] fzf integration
- [x] implement user history 
- [x] test it myself a week before merging to main


# Posible problems
not updating stocks in db when api calls from bet session 
