UPDATE responses
SET correct = ?
WHERE question_id = ? AND user_id = ? AND timestamp = ?;
