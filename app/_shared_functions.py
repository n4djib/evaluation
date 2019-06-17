from app import app
from ast import literal_eval


def extract_fields(formula):
    fields_list = []
    dictionary = eval(formula)
    for key in dictionary:
        fields_list += [key]

    return fields_list

def check_grades_status(grades):
    # return a dictionary
    #   of errors and empty and calculated
    nbr_cells = 0
    nbr_filled = 0
    nbr_errs = 0

    EMPTY = False
    ERRS = False
    CALC = False

    for grade in grades:
        fields_list = []
        if grade.formula != None:
            fields_list = extract_fields(grade.formula)
        for field in fields_list:
            if field in ['cour', 'td', 'tp', 't_pers', 'stage']:
                nbr_cells += 1
                val = getattr(grade, field)
                if val != None:
                    nbr_filled += 1
                    # if val < 0  or  val > 20  or  not isinstance(val, decimal.decimal):
                    if val < 0  or  val > 20:
                        nbr_errs += 1
                        ERRS = True

        # CALC
        if grade.is_dirty == True:
            CALC = True
    # end for

    if nbr_cells != nbr_filled:
        EMPTY = True

    return {'nbr_cells': nbr_cells, 'nbr_filled': nbr_filled,
            'EMPTY': EMPTY, 'nbr_empty': nbr_cells - nbr_filled, 
            'ERRS': ERRS, 'nbr_errs': nbr_errs, 'CALC': CALC}

def check_session_is_complite(grades, session):
    CONF = session.is_config_changed()
    status = check_grades_status(grades)
    status['CONF'] = CONF
    if (status['nbr_cells'] == 0 
        and not session.is_historic() 
        and len(session.student_sessions) > 0):
        status['need_init'] = True
    return status
