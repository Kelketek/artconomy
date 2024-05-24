<template>
  <div class="flex flex-column">
    <div class="flex">
      <v-toolbar dense color="secondary">
        <v-toolbar-title>Journals</v-toolbar-title>
        <v-spacer/>
        <v-btn color="green" @click="showNew = true" v-if="isCurrent" variant="flat">
          <v-icon left :icon="mdiPlus"/>
          Add New
        </v-btn>
      </v-toolbar>
      <v-col class="elevation-4">
        <ac-paginated :list="journals">
          <v-col cols="12">
            <v-list two-line>
              <template v-for="item in journals.list" :key="item.x!.id">
                <v-list-item
                    :to="{name: 'Journal', params: {username, journalId: item.x!.id}}"
                    v-if="item.x!"
                >
                  <template v-slot:prepend>
                    <v-icon :icon="mdiPencil"/>
                  </template>
                  <v-list-item-title>{{item.x!.subject}}</v-list-item-title>
                  <v-list-item-subtitle>{{formatDate(item.x!.created_on)}}</v-list-item-subtitle>
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
          <ac-bound-field :field="newJournal.fields.subject" label="Subject" autofocus/>
        </v-col>
        <v-col cols="12" sm="10" offset-sm="1" offset-md="2" md="8">
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

<script setup lang="ts">
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import {Journal} from '@/types/Journal.ts'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {mdiPencil, mdiPlus} from '@mdi/js'
import {computed, ref} from 'vue'
import SubjectiveProps from '@/types/SubjectiveProps.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {useList} from '@/store/lists/hooks.ts'
import {useRouter} from 'vue-router'
import {useSubject} from '@/mixins/subjective.ts'
import {formatDate} from '@/lib/otherFormatters.ts'

const props = defineProps<SubjectiveProps>()
const {isCurrent} = useSubject(props)
const router = useRouter()
const showNew = ref(false)
const url = computed(() => `/api/profiles/account/${props.username}/journals/`)

const newJournal = useForm(props.username + '-newJournal', {
  endpoint: url.value,
  fields: {
    subject: {
      value: '',
      validators: [{name: 'required'}],
    },
    body: {
      value: '',
      validators: [{name: 'required'}],
    },
    comments_disabled: {value: false},
  },
})
const journals = useList<Journal>(props.username + '-journals', {
  endpoint: url.value,
  params: {size: 3},
})
journals.firstRun().then()

const visitJournal = (response: Journal) => {
  router.push({
    name: 'Journal',
    params: {
      username: props.username,
      journalId: response.id + '',
    },
  })
}
</script>
