SELECT 
  id,
  question,
  outcome_probs,
  outcomes,
  tag,
  outcome,
  end_date,
  description
FROM questions WHERE id = ?;
