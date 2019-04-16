<template>
  <div>
    <div class="textualized">
      {{textualize(toText)}}
    </div>
    <div class="datestring">
      {{formatDate(dateString)}}
    </div>
    <div class="tersedatestring">
      {{formatDateTerse(dateString)}}
    </div>
    <div class="truncatable">
      {{truncateText(truncatable, 10)}}
    </div>
  </div>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Formatting from '@/mixins/formatting'

  @Component
export default class FormattedComponent extends mixins(Formatting) {
    public toText = '# Hello!'
    public dateString = '2020-08-10'
    public truncatable = 'This is a test. Please enjoy the test.'

    public get nameCheck() {
      return this.guestName('Guest #3')
    }
}
</script>
