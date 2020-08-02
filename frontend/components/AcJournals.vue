<template>
  <div class="flex flex-column">
    <div class="flex">
      <v-toolbar dense color="secondary">
        <v-toolbar-title>Journals</v-toolbar-title>
        <v-spacer />
        <v-btn color="green" @click="showNew = true" v-if="isCurrent"><v-icon left>add</v-icon>Add New</v-btn>
      </v-toolbar>
      <v-col class="elevation-4">
        <ac-paginated :list="journals">
          <v-col cols="12">
            <v-list two-line>
              <template v-for="item in journals.list">
                <v-list-item
                  :key="item.x.id"
                  :to="{name: 'Journal', params: {username, journalId: item.x.id}}"
                >
                  <v-list-item-avatar>
                    <v-icon>edit</v-icon>
                  </v-list-item-avatar>
                  <v-list-item-content>
                    <v-list-item-title>{{item.x.subject}}</v-list-item-title>
                    <v-list-item-subtitle>{{formatDate(item.x.created_on)}}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </template>
            </v-list>
          </v-col>
        </ac-paginated>
      </v-col>
    </div>
    <ac-form-dialog
        v-model="showNew"
        v-if="isCurrent"
        v-bind="newJournal.bind"
        @submit="newJournal.submitThen(visitJournal)"
        :large="true"
        title="New Journal"
    >
      <v-row>
        <v-col cols="12" sm="10" offset-sm="1" offset-md="2" md="8">
          <ac-bound-field :field="newJournal.fields.subject" label="Subject" autofocus />
        </v-col>
        <v-col cols="12" sm="10" offset-sm="1" offset-md="2" md="8" >
          <ac-bound-field :field="newJournal.fields.body" field-type="ac-editor" label="Body"
                          :auto-save="true" :save-indicator="false"
          />
        </v-col>
        <v-col cols="12" sm="10" offset-sm="1" offset-md="2" md="8">
          <ac-bound-field :field="newJournal.fields.comments_disabled" field-type="ac-checkbox" :persistent-hint="true"
                          label="Comments Disabled"
                          hint="If checked, prevents people from commenting on this journal."
          />
        </v-col>
      </v-row>
    </ac-form-dialog>
  </div>
</template>

<script lang="ts">
// import Paginated from './mixins/paginated'
import Formatting from '@/mixins/formatting'
import {truncateText} from '@/lib/lib'
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import {Journal} from '@/types/Journal'
import {ListController} from '@/store/lists/controller'
import {FormController} from '@/store/forms/form-controller'
import AcBoundField from '@/components/fields/AcBoundField'
import AcRendered from '@/components/wrappers/AcRendered'
import AcLoadingSpinner from '@/components/wrappers/AcLoadingSpinner.vue'
import AcGrowSpinner from '@/components/AcGrowSpinner.vue'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'

  @Component({
    components: {AcPaginated, AcGrowSpinner, AcLoadingSpinner, AcRendered, AcBoundField, AcFormDialog},
  })
export default class AcJournals extends mixins(Subjective, Formatting) {
    public firstRun: boolean = true
    public currentJournal: null|Journal = null
    public showNew = false
    public journals: ListController<Journal> = null as unknown as ListController<Journal>
    public newJournal: FormController = null as unknown as FormController

    public created() {
      this.newJournal = this.$getForm(this.username + '-newJournal', {
        endpoint: this.url,
        fields: {
          subject: {value: '', validators: [{name: 'required'}]},
          body: {value: '', validators: [{name: 'required'}]},
          comments_disabled: {value: false},
        },
      })
      this.journals = this.$getList(this.username + '-journals', {endpoint: this.url, pageSize: 3})
      this.journals.firstRun().then()
    }

    public visitJournal(response: Journal) {
      this.$router.push({name: 'Journal', params: {username: this.username, journalId: response.id + ''}})
    }

    public get url() {
      return `/api/profiles/v1/account/${this.username}/journals/`
    }

    public get preview() {
      if (!this.currentJournal) {
        return ''
      }
      return truncateText(this.currentJournal.body, 1000)
    }
}
</script>
