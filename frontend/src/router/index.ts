import { createRouter, createWebHistory } from 'vue-router'
import ProcessView from '../views/ProcessView.vue'
import ExamView from '../views/ExamView.vue'
import ProgressView from '../views/ProgressView.vue'

const router = createRouter({
  history: createWebHistory(),
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
    }
  ]
})

export default router
