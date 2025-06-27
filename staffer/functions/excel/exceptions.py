class ExcelError(Exception):
    """Base exception for Excel operations in Staffer."""
    pass

class WorkbookError(ExcelError):
    """Raised when workbook operations fail."""
    pass

class SheetError(ExcelError):
    """Raised when sheet operations fail."""
    pass

class DataError(ExcelError):
    """Raised when data operations fail."""
    pass

class ValidationError(ExcelError):
    """Raised when validation fails."""
    pass

class FormattingError(ExcelError):
    """Raised when formatting operations fail."""
    pass

class CalculationError(ExcelError):
    """Raised when formula calculations fail."""
    pass

class PivotError(ExcelError):
    """Raised when pivot table operations fail."""
    pass

class ChartError(ExcelError):
    """Raised when chart operations fail."""
    pass
