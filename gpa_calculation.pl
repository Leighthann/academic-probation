% Store default GPA threshold (Academic Probation Limit)
default_gpa(2.0).


% Student records: student(StudentID, Name, Programme, School).
student(1001, 'John Doe', 'Computer Science', 'SCIT').
student(1002, 'Jane Smith', 'Information Technology', 'SCIT').

% Module details: module(ModuleCode, Credits).
module(cs101, 3).
module(cs102, 4).
module(cs103, 3).
module(cs104, 4).

% Student grades: grade(StudentID, ModuleCode, GradePoint).
grade(1001, cs101, 3.5).
grade(1001, cs102, 4.0).
grade(1001, cs103, 2.5).
grade(1001, cs104, 3.0).

grade(1002, cs101, 2.0).
grade(1002, cs102, 1.5).
grade(1002, cs103, 2.0).
grade(1002, cs104, 1.8).

% GPA calculation predicate that takes a list of (GradePoint, Credits) pairs
gpa([], 0.0).  % Base case: empty list returns 0.0
gpa(List, GPA) :-
    calculate_total_points(List, TotalPoints),
    calculate_total_credits(List, TotalCredits),
    TotalCredits > 0,  % Prevent division by zero
    GPA is TotalPoints / TotalCredits.

% Calculate total points (sum of GradePoint * Credits)
calculate_total_points([], 0).
calculate_total_points([(GP, C)|Rest], Total) :-
    calculate_total_points(Rest, RestTotal),
    Total is (GP * C) + RestTotal.

% Calculate total credits
calculate_total_credits([], 0).
calculate_total_credits([(_, C)|Rest], Total) :-
    calculate_total_credits(Rest, RestTotal),
    Total is C + RestTotal.

% Check if GPA is below probation threshold (2.0)
check_academic_probation(GPA) :-
    GPA < 2.0.

% Calculate cumulative GPA assuming two semesters
cumulative_gpa(StudentID, CGPA) :-
    gpa(StudentID, GPA1),
    gpa(StudentID, GPA2),
    total_credits(StudentID, Credits1),
    total_credits(StudentID, Credits2),
    TotalCredits is Credits1 + Credits2,
    TotalGP is (GPA1 * Credits1) + (GPA2 * Credits2),
    TotalCredits > 0,
    CGPA is TotalGP / TotalCredits.

% Check if student is on academic probation
academic_probation(StudentID) :-
    cumulative_gpa(StudentID, CGPA),
    default_gpa(Threshold),
    CGPA =< Threshold.

% Update default GPA threshold
update_default_gpa(NewGPA) :-
    retractall(default_gpa(_)),
    assertz(default_gpa(NewGPA)).



