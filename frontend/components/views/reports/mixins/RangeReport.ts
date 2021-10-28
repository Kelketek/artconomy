import Component from 'vue-class-component'
import Vue from 'vue'

@Component
export default class RangeReport extends Vue {
  public startDate = ''
  public endDate = ''
  public get rangeKwargs() {
    const kwargs: {[key: string]: string} = {}
    if (this.startDate) {
      kwargs.start_date = this.startDate
    }
    if (this.endDate) {
      kwargs.end_date = this.endDate
    }
    return kwargs
  }

  public get rangeString() {
    const str = Object.keys(this.rangeKwargs).map(key => key + '=' + this.rangeKwargs[key]).join('&')
    if (str) {
      return `?${str}`
    }
    return ''
  }
}
