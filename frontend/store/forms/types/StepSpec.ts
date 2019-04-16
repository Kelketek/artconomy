export default interface StepSpec {
  failed: boolean,
  complete: boolean,
  rules: Array<() => boolean>
}
