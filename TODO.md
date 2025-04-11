# TODO

- [X] tests for insert_user_by_name and replace insert_user
- [X] implement update database
    - update questions
    - if a question is solved update all its responses and transactions and update users stats
    - notify of new stats of users 
- [x] implement betting system
    - [x] cli
        - [x] transaction prompt
            - [x] main functionailty
            - [x] better prints
        - [x] portfolio choice to sell
    - [x] perform transaction
    - [x] update database
        - [x] inform users of stock change upon updating
        - [X] automatic stock sells upon market completion   
- [ ] fzf integration
- [x] implement user history 


# Posible problems
not updating stocks in db when api calls from bet session 
