<template>
  <v-flex>
    <v-layout row wrap>
      <v-flex xs12 text-xs-center>
        Try terms like:
        <p><v-chip color="secondary" @click="search('fox')">fox</v-chip>
        <v-chip color="secondary" @click="search('pony')">pony</v-chip>
        <v-chip color="secondary" @click="search('chibi')">chibi</v-chip>
        <v-chip color="secondary" @click="search('refsheet')">refsheet</v-chip></p>
      </v-flex>
    </v-layout>
  </v-flex>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import SearchHints from '@/components/views/search/mixins/SearchHints'
import AcBoundField from '@/components/fields/AcBoundField'
import Viewer from '@/mixins/viewer'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
  @Component({
    components: {AcExpandedProperty, AcBoundField},
  })
export default class SubmissionHints extends mixins(SearchHints, Viewer) {
}
</script>
