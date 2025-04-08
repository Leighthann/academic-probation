% GPA Calculation in Prolog
% Base case: Empty list results in GPA of 0
gpa([], 0.0).

gpa(GradesCredits, GPA) :-
    sum_grade_points_and_credits(GradesCredits, TotalGradePoints, TotalCredits),
    (   TotalCredits > 0
    ->  GPA is TotalGradePoints / TotalCredits
    ;   GPA is 0.0  % Avoid division by zero
    ).

% Helper predicate to sum grade points and credits
sum_grade_points_and_credits([], 0, 0).
sum_grade_points_and_credits([(GradePoint, Credits) | Rest], TotalGradePoints, TotalCredits) :-
    sum_grade_points_and_credits(Rest, SumRestGradePoints, SumRestCredits),
    TotalGradePoints is SumRestGradePoints + (GradePoint * Credits),
    TotalCredits is SumRestCredits + Credits.

% Default GPA threshold for academic probation
:- dynamic default_gpa_threshold/1.

% Load the GPA threshold from the file (if it exists)
:- [gpa_threshold].

% Check if the GPA is below the default threshold
check_academic_probation(GPA, IsProbation) :-
    default_gpa_threshold(Threshold),
    (   GPA < Threshold
    ->  IsProbation = true
    ;   IsProbation = false
    ).

% Update the GPA threshold and save it permanently
set_gpa_threshold(NewThreshold) :-
    retractall(default_gpa_threshold(_)),  % Remove existing threshold
    assertz(default_gpa_threshold(NewThreshold)),  % Add the new threshold
    save_gpa_threshold(NewThreshold).  % Save it to a file

% Save the updated GPA threshold to a file
save_gpa_threshold(NewThreshold) :-
    open('gpa_threshold.pl', write, Stream),  % Open file in write mode
    write(Stream, ':- dynamic default_gpa_threshold/1.'), nl(Stream),
    write(Stream, 'default_gpa_threshold('), write(Stream, NewThreshold), write(Stream, ').'), nl(Stream),
    close(Stream).  % Close the file
