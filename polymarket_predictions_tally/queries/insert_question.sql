-- Add a new question
INSERT INTO questions (id, question, tag, end_date, description, outcome, outcome_probs, outcomes)
VALUES (?, ?, ?, ?, ?, ?, ?, ?);
