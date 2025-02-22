UPDATE stats
  SET correct_answers = correct_answers + ?,
  incorrect_answers = incorrect_answers + ?
  WHERE user_id = ?;

