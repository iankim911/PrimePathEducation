import Link from 'next/link'

export default function CRMDashboard() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Welcome Section */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          CRM Dashboard
        </h2>
        <p className="text-gray-600">
          Manage your academy's daily operations, students, and staff
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-2xl font-bold text-gray-900">0</div>
          <div className="text-sm text-gray-600">Active Students</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-2xl font-bold text-gray-900">0</div>
          <div className="text-sm text-gray-600">Classes</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-2xl font-bold text-gray-900">0</div>
          <div className="text-sm text-gray-600">Teachers</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-2xl font-bold text-gray-900">0</div>
          <div className="text-sm text-gray-600">Today's Attendance</div>
        </div>
      </div>

      {/* Module Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Academic Management */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Academic Management</h3>
          <div className="space-y-3">
            <Link href="/students" className="block text-gray-600 hover:text-gray-900 hover:bg-gray-50 p-2 rounded">
              → Students
            </Link>
            <Link href="/classes" className="block text-gray-600 hover:text-gray-900 hover:bg-gray-50 p-2 rounded">
              → Classes
            </Link>
            <Link href="/enrollments" className="block text-gray-600 hover:text-gray-900 hover:bg-gray-50 p-2 rounded">
              → Enrollments
            </Link>
            <Link href="/attendance" className="block text-gray-600 hover:text-gray-900 hover:bg-gray-50 p-2 rounded">
              → Attendance
            </Link>
          </div>
        </div>

        {/* Staff Management */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Staff Management</h3>
          <div className="space-y-3">
            <Link href="/teachers" className="block text-gray-600 hover:text-gray-900 hover:bg-gray-50 p-2 rounded">
              → Teachers
            </Link>
            <Link href="/teachers" className="block text-gray-600 hover:text-gray-900 hover:bg-gray-50 p-2 rounded">
              → Teacher Assignments
            </Link>
            <Link href="/curriculum" className="block text-gray-600 hover:text-gray-900 hover:bg-gray-50 p-2 rounded">
              → Curriculum Setup
            </Link>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <Link href="/students" className="block bg-gray-900 text-white text-center px-4 py-2 rounded hover:bg-gray-800">
              Add New Student
            </Link>
            <Link href="/classes" className="block bg-gray-900 text-white text-center px-4 py-2 rounded hover:bg-gray-800">
              Create Class
            </Link>
            <Link href="/teachers" className="block bg-gray-900 text-white text-center px-4 py-2 rounded hover:bg-gray-800">
              Add Teacher
            </Link>
            <Link href="/attendance" className="block bg-gray-900 text-white text-center px-4 py-2 rounded hover:bg-gray-800">
              Take Attendance
            </Link>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="mt-8 bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        <div className="text-gray-500">
          <p>No recent activity to display</p>
        </div>
      </div>
    </div>
  )
}