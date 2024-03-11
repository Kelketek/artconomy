<template>
  <v-col>
    <v-row no-gutters>
      <v-col class="text-center" cols="12">
        Try terms like:
        <p>
          <v-chip color="secondary" variant="flat" @click="search('fox')" class="mx-1">fox</v-chip>
          <v-chip color="secondary" variant="flat" @click="search('pony')" class="mx-1">pony</v-chip>
          <v-chip color="secondary" variant="flat" @click="search('chibi')" class="mx-1">chibi</v-chip>
          <v-chip color="secondary" variant="flat" @click="search('refsheet')" class="mx-1">refsheet</v-chip>
        </p>
      </v-col>
    </v-row>
  </v-col>
</template>

<script setup lang="ts">
import {useForm} from '@/store/forms/hooks.ts'

const searchForm = useForm('search')
const search = (val: string) => searchForm.fields.q.model = val
</script>
