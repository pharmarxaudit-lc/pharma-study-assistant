import { createRouter, createWebHashHistory } from 'vue-router'
import ProcessView from '../views/ProcessView.vue'
import ExamView from '../views/ExamView.vue'
import ProgressView from '../views/ProgressView.vue'
import TestView from '../views/TestView.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      redirect: '/process'
    },
    {
      path: '/process',
      name: 'process',
      component: ProcessView,
      meta: { title: 'Process PDFs' }
    },
    {
      path: '/exam',
      name: 'exam',
      component: ExamView,
      meta: { title: 'Exam Prep' }
    },
    {
      path: '/progress',
      name: 'progress',
      component: ProgressView,
      meta: { title: 'Progress' }
    },
    {
      path: '/test',
      name: 'test',
      component: TestView,
      meta: { title: 'Mock Screens' }
    }
  ]
})

export default router
