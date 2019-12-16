<template>
  <v-row no-gutters>
    <v-col cols="12" class="text-center" v-if="isRegistered">
      <v-expansion-panels v-model="panel">
        <v-expansion-panel>
          <v-expansion-panel-header class="pa-1">
            <v-row no-gutters>
              <v-col class="text-center extra-height">
                <v-icon left>settings</v-icon>Search Options
                <v-chip v-if="searchForm.fields.watch_list.value" color="primary" class="mx-1">watchlist</v-chip>
              </v-col>
            </v-row>
          </v-expansion-panel-header>
          <v-expansion-panel-content>
            <v-card-text>
              <v-row no-gutters>
                <v-col cols="12" sm="6" md="4">
                  <ac-bound-field
                      :field="searchForm.fields.watch_list"
                      field-type="v-checkbox"
                      label="Watch List"
                      :persistent-hint="true"
                      hint="Only return results from artists on my watch list."
                  />
                </v-col>
              </v-row>
            </v-card-text>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-col>
  </v-row>
</template>

<style scoped>
  .extra-height {
    line-height: 2.5;
  }
</style>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import SearchHints from '../mixins/SearchHints'
import AcBoundField from '@/components/fields/AcBoundField'
import Viewer from '@/mixins/viewer'
  @Component({
    components: {AcBoundField},
  })
export default class SubmissionExtra extends mixins(SearchHints, Viewer) {
    public panel: null|number = null
}
</script>
