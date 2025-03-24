INSERT INTO positions (user_id, question_id, stake_yes, stake_no)
VALUES (?, ?, ?, ?)
ON CONFLICT(user_id, question_id)
DO UPDATE SET stake_yes = ?, stake_no = ?;
