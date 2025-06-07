import coverage
import unittest

cov = coverage.Coverage(source=[
    "point_range",
    "program_start",
    "set_of_request",
    "work_exit",
    "machine_swich",
    "default_control",
    "company_location"
])
cov.start()

suite = unittest.defaultTestLoader.discover('.', pattern='test_*.py')
unittest.TextTestRunner().run(suite)

cov.stop()
cov.save()
cov.report(show_missing=True)  # 콘솔 출력
cov.html_report(directory='coverage_html_report')  # HTML 리포트 생성
print("HTML 커버리지 리포트가 'coverage_html_report' 폴더에 생성되었습니다.")