<template>
  <v-col>
    <v-row no-gutters  >
      <v-col class="text-center" cols="12" >
        Try terms like:
        <p><v-chip color="secondary" @click="search('fox')" class="mx-1">fox</v-chip>
        <v-chip color="secondary" @click="search('pony')" class="mx-1">pony</v-chip>
        <v-chip color="secondary" @click="search('chibi')" class="mx-1">chibi</v-chip>
        <v-chip color="secondary" @click="search('refsheet')" class="mx-1">refsheet</v-chip></p>
      </v-col>
    </v-row>
  </v-col>
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
