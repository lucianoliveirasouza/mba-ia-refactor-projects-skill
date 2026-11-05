const { PAYMENT_STATUS, UNKNOWN_STUDENT_NAME } = require('../constants');

function createReportController({ enrollmentModel }) {
    return {
        async financialReport() {
            const rows = await enrollmentModel.findFinancialRows();
            const byCourse = new Map();

            for (const row of rows) {
                if (!byCourse.has(row.course_id)) {
                    byCourse.set(row.course_id, { course: row.course_title, revenue: 0, students: [] });
                }
                if (row.enrollment_id === null) continue;

                const entry = byCourse.get(row.course_id);
                if (row.payment_status === PAYMENT_STATUS.PAID) entry.revenue += row.payment_amount;
                entry.students.push({
                    student: row.student_name ?? UNKNOWN_STUDENT_NAME,
                    paid: row.payment_amount ?? 0,
                });
            }

            return [...byCourse.values()];
        },
    };
}

module.exports = { createReportController };
