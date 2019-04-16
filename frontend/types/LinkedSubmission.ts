import Submission from '@/types/Submission'

export default interface LinkedSubmission {
  id: number,
  submission: Submission,
  submission_id?: number,
}
