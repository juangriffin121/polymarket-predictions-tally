SELECT user_id, question_id, answer, timestamp, correct, explanation FROM responses
WHERE user_id = ? AND question_id = ?; 
